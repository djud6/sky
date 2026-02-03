import React, {useState, useEffect} from "react";
import axios from "axios";
import {useSelector} from "react-redux";
import {getAuthHeader} from "../../helpers/Authorization";
import * as Constants from "../../constants";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../ShareComponents/CustomInputText";
import FileUploadInput from "../ShareComponents/FileUploadInput";
import {loadingAlert, successAlert, generalErrorAlert} from "../ShareComponents/CommonAlert";
import {useTranslation} from "react-i18next";
import {Button} from "primereact/button";
import {Dialog} from "primereact/dialog";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/dialogStyles.scss";
import CustomTextArea from "../ShareComponents/CustomTextArea";
import {Checkbox} from "primereact/checkbox";
import Tooltip from "../ShareComponents/Tooltip/Tooltip";

const AddCustomField = ({vehicle, dialogStatus, setDialogStatus, setForceUpdate}) => {
        const {t} = useTranslation();
        const dataType = [
            {
                name: t("addCustomField.data_type_default"),
                code: "",
            },
            {
                name: t("addCustomField.data_type_text"),
                code: "Text",
            },
            {
                name: t("addCustomField.data_type_number"),
                code: "Number",
            },
            {
                name: t("addCustomField.data_type_date"),
                code: "Date",
            },

        ];

        const newFieldOptions = [
            {
                name: t("addCustomField.new_field_option_default"),
                code: "",
            },
            {
                name: t("addCustomField.new_field_option1"),
                code: "PTO",
            },
            {
                name: t("addCustomField.new_field_option2"),
                code: "Tire Pressure",
            },
        ];

        let defaultD = dataType.find((option) => option.code === "");
        if (defaultD === "Dropdown") {
            defaultD = "";
        }
        const defaultN = newFieldOptions.find((option) => option.code === "");
        const [selectedDataType, setSelectedDataType] = useState(defaultD);
        const [selectedNewField, setSelectedNewField] = useState(defaultN);
        const [assetsList, setAssetsList] = useState([])
        const [fileLoading, setFileLoading] = useState(false);
        const [selectedApplyToSimilar, setSelectedApplyToSimilar] = useState(false);


        const [newFieldInfo, setNewFieldInfo] = useState({
            new_field_one: "",
            data_type: "",
            new_field_value: "",
        });

        useEffect(() => {
            setNewFieldInfo({
                new_field_one: selectedNewField.code,
                data_type: selectedDataType.code,
                new_field_value: newFieldInfo.new_field_value,
            })

            const defaultD = dataType.find((option) => option.code === "");
            setSelectedDataType(defaultD);

            const defaultN = newFieldOptions.find((option) => option.code === "");
            setSelectedNewField(defaultN);

            // eslint-disable-next-line react-hooks/exhaustive-deps
        }, [vehicle]);

    const handleAssetUpdate = () => {
        // Create a copy of the existing assetUpdateData
        const updatedData = { ...vehicle.custom_fields };

        updatedData[`field1`] = {
                name: newFieldInfo.new_field_one,
                type: selectedDataType.code,
                value: newFieldInfo.new_field_value,

        };

        handleUpdateSubmit(updatedData);
    };


        useEffect(() => {
            axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/All`, getAuthHeader())
                .then((response) => {
                    setAssetsList(response.data)
                })
        }, [getAuthHeader])

        const handleUpdateSubmit = (data) => {
            loadingAlert();

            const handleAssetPost = (VIN, data) => {
                return axios
                    .post(
                        `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Add/CustomField/${VIN}`,
                        data,
                        getAuthHeader()
                    )
                    .then((res) => {
                        return res.data; // Optionally return the result to be used in Promise.all()
                    });
            };

            axios
                .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/VIN/${vehicle.VIN}`, getAuthHeader())
                .then((response) => {
                    let assetType = response.data.asset_type;
                    let sorted = assetsList
                        .filter((el) => el.asset_type === assetType)
                        .map((el) => el.VIN);
                    if (selectedApplyToSimilar === true) {
                        // Using Promise.all() to wait for all POST requests to finish
                        return Promise.all(
                            sorted.map((el) => handleAssetPost(el, data))
                        );
                    } else handleAssetPost(vehicle.VIN, data)
                })
                .then((results) => {
                    // All POST requests are completed successfully
                    successAlert(t("updateAsset.update_asset"));
                    setDialogStatus(false);
                    setForceUpdate(Date.now());
                })
                .catch((error) => {
                    // Handle errors here
                    console.error("Error:", error);
                    // Optionally handle error for each individual request
                    // For example, you can check if it's an Axios error with error.response and error.request
                });
        };

        const renderFooter = () => {
            return (
                <div>
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        className="p-button-text"
                        onClick={() => setDialogStatus(false)}
                    />
                    <Button
                        label="Confirm"
                        icon="pi pi-check"
                        onClick={handleAssetUpdate}
                        disabled={fileLoading}
                    />
                </div>
            );
        };

        const selectDataType = (code) => {
            let selected = dataType.find((op) => op.code === code);
            setNewFieldInfo({...newFieldInfo, data_type: selected.code});
        };


        return (
            <React.Fragment>
                <Dialog
                    className="custom-main-dialog"
                    header={t("addCustomField.add_custom_field_title")}
                    visible={dialogStatus}
                    onHide={() => setDialogStatus(false)}
                    style={{width: "50vw"}}
                    breakpoints={{"1440px": "75vw", "980px": "85vw", "600px": "90vw"}}
                    footer={renderFooter()}
                >
                    <div className="p-field">
                        <label>{t("addCustomField.new_field1")}</label>
                        <CustomInputText
                            className="w-100"
                            value={newFieldInfo["new_field_one"]}
                            onChange={(val) => setNewFieldInfo({...newFieldInfo, new_field_one: val})}
                            leftStatus
                        />
                    </div>

                    <div className="p-field">
                        <label>{t("addCustomField.new_field1_type")}</label>
                        <FormDropdown
                            onChange={selectDataType}
                            options={dataType.filter(el => el.code !== "")} defaultValue={selectedDataType}
                            dataReady={selectedDataType}
                            plain_dropdown
                            leftStatus
                            reset={"disabled"}
                        />
                    </div>

                    <div className="p-field">
                        <label className="h6">{t("addCustomField.new_field1_value")}</label>
                        <CustomInputText
                            className="w-100"
                            type={newFieldInfo.data_type}
                            value={newFieldInfo["new_field"]}
                            onChange={(val) => setNewFieldInfo({...newFieldInfo, new_field_value: val})}
                            leftStatus
                        />
                        <div className="p-d-flex p-jc-end p-mt-3 sub-form apply-similar">
                            <div className="p-d-flex">
                                <Checkbox
                                    onChange={(e) => setSelectedApplyToSimilar(e.checked)}
                                    checked={selectedApplyToSimilar}
                                />
                                <div className="apply-text">
                                    {t("addCustomField.apply_to_all_label")}
                                </div>
                                <Tooltip
                                    label={"tooltip-all"}
                                    description={t("addCustomField.tooltip_apply_all")}
                                />
                            </div>
                        </div>
                    </div>

                </Dialog>
            </React.Fragment>
        );
    }
;

export default AddCustomField;
