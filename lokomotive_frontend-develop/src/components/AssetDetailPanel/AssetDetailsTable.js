import React, {useEffect, useState} from "react";
import {useTranslation} from "react-i18next";
import {capitalize} from "../../helpers/helperFunctions";
import * as Constants from "../../constants";
import axios from "axios";
import {loadingAlert, successAlert, generalErrorAlert} from "../ShareComponents/CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import {getAuthHeader} from "../../helpers/Authorization";

const AssetDetailsTable = ({asset, vin}) => {
    const {t} = useTranslation();
    const [newFieldsData, SetNewFieldsData] = useState("");
    useEffect(() => {
        if (vin) {
            const getNewFieldsTitles = async () => {
                try {
                    await axios
                        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/VIN/${vin}`, getAuthHeader())
                        .then((res) => {
                            if (res.data.custom_fields) {
                                // SetNewFieldsData(res.data.custom_fields.toString().split("!"));
                                // console.log(res.data.custom_fields.toString().split("!"));

                            }
                        })
                        .catch((error) => {
                            ConsoleHelper(error);
                            generalErrorAlert(error.customErrorMsg);
                        });
                } catch (error) {
                    ConsoleHelper(error);
                    generalErrorAlert(error.customErrorMsg);
                }
            };
            getNewFieldsTitles();
        }
    }, []);

    const setFields = () => {
        for (let i = 2; i < newFieldsData.length; i += 8) {
            return (
                <div>
                    <div className="p-d-flex p-jc-between">
                        <span className="left-title-section">{newFieldsData[i]}</span>
                        <span className="right-value-section text-right">{newFieldsData[i + 4]}</span>
                    </div>
                    <hr className="solid"/>
                </div>
            );
        }
    };

    let tableTitles = [
        t("assetDetailPanel.status_label"),
        t("assetDetailPanel.unit_number_label"),
        t("assetDetailPanel.asset_type_label"),
        t("general.model_number"),
        t("assetDetailPanel.business_unit_label"),
        t("assetDetailPanel.location_label"),
        t("assetDetailPanel.manufacturer_label"),
        t("assetDetailPanel.company_label"),
        t("assetDetailPanel.year_of_manufacture"),
        t("assetDetailPanel.fuel_type_label"),
        t("assetDetailPanel.license_plate_label"),
        t("assetDetailPanel.parent_asset_label"),
        t("assetDetailPanel.child_assets_label"),
        ...(asset.hours_or_mileage.toLowerCase() === "hours" ||
        asset.hours_or_mileage.toLowerCase() === "both"
            ? [t("assetDetailPanel.hours_label"), t("assetDetailPanel.daily_average_hours")]
            : []),
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
            ? [t("assetDetailPanel.mileage_label"), t("assetDetailPanel.daily_average_mileage")]
            : []),
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
            ? [t("assetDetailPanel.mileage_unit")]
            : []),
        t("assetDetailPanel.total_cost"),
        t("assetDetailPanel.description"),
        (asset.custom_fields)?(capitalize(asset.custom_fields.field1.name)):undefined
    ];
    let tableValues = [
        asset.status,
        asset.unit_number || t("general.not_applicable"),
        asset.asset_type || t("general.not_applicable"),
        asset.model_number || t("general.not_applicable"),
        asset.businessUnit || t("general.not_applicable"),
        asset.current_location || t("general.not_applicable"),
        asset.manufacturer || t("general.not_applicable"),
        asset.company || t("general.not_applicable"),
        asset.date_of_manufacture || t("general.not_applicable"),
        capitalize(asset.fuel_type) || t("general.not_applicable"),
        asset.license_plate || t("general.not_applicable"),
        asset.parent || t("general.not_applicable"),
        asset.children.length !== 0
            ? [
                asset.children.length > 1 &&
                asset.children.map((child) => {
                    return child + ", ";
                }),
            ]
            : [t("general.not_applicable")],
        ...(asset.hours_or_mileage.toLowerCase() === "hours" ||
        asset.hours_or_mileage.toLowerCase() === "both"

            ? [asset.hours.toLocaleString(), asset.daily_average_hours.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })]
            : []),
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
            ? [asset.mileage.toLocaleString(), asset.daily_average_mileage.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })]

            : []),
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
            ? [asset.mileage_unit || t("general.not_applicable")]
            : []),

       "$ " + asset.total_cost.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }) || t("general.not_applicable"),
        asset.asset_description || t("general.not_applicable"),
        (asset.custom_fields)?capitalize(asset.custom_fields.field1.value):undefined
    ]
    return (
        <div className="p-d-flex p-flex-column asset-details-table">
            {tableTitles &&
                tableTitles.filter(el=>el!==null&&el!==""&&el!==undefined).map((title, index) => {
                    return (
                        <div key={index}>
                            <div className="p-d-flex p-jc-between">
                                <span className="left-title-section">{title}</span>
                                <span className="right-value-section text-right">{tableValues[index]}</span>
                            </div>
                            <hr className="solid"/>
                        </div>
                    );
                })}

            {
                newFieldsData &&
                (newFieldsData.length <= 1 ?
                        setFields() :
                        (newFieldsData.map((title, index) => {
                                return (
                                    <div key={index}>
                                        <div className="p-d-flex p-jc-between">
                                            <span className="left-title-section">1</span>
                                            <span
                                                className="right-value-section text-right">{newFieldsData[index]}</span>
                                        </div>
                                        <hr className="solid"/>
                                    </div>
                                );
                            })
                        )
                )
            }
        </div>
    );
};

export default AssetDetailsTable;
