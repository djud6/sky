import React, {useState, useEffect} from "react";
import {useTranslation} from "react-i18next";
import axios from "axios";
import {faUsers} from "@fortawesome/free-solid-svg-icons";
import {Button} from "primereact/button";
import {Dropdown} from "primereact/dropdown";
import "../../../styles/ShareComponents/GeneralRadio.scss";
import {InputSwitch} from "primereact/inputswitch";
import {getAuthHeader, getRolePermissions} from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/AccountOptions/ManageNotifications.scss";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import {RadioButton} from "primereact/radiobutton";
import {value} from "lodash/seq";


let selectedNotification = {};
//due date management json
let dueDateDataJSON = {};
//all the notification data to be updated
let notificationUpdateDataJSON = {};

const ManageNotifications = () => {
    const {t} = useTranslation();
    const [dataReady, setDataReady] = useState(false);
    const [notificationTriggers, setNotificationTriggers] = useState(null);
    //store all the dropdown values
    const [businessTriggers, setBusinessTriggers] = useState(null);
    const [locationTriggers, setLocationTriggers] = useState(null);
    const [roleTriggers, setRoleTriggers] = useState(null);
    const [userTriggers, setUserTriggers] = useState(null);
    const [assetTriggers, setAssetTriggers] = useState(null);
    const [assetTypeTriggers, setAssetTypes] = useState(null);
    //notification type selected
    const [selectedValue, setSelectedValue] = useState("");
    //if active or enable switch is clicked
    const [isActivated, setIsActivated] = useState();
    const [isEnabled, setIsEnabled] = useState();

    // custom email text
    const [customText, setCustomText] = useState("");

    //if any dropdown value is selected
    const [selectedBusinessUnit, setSelectedBusinessUnit] = useState([]);
    const [selectedLocation, setSelectedLocation] = useState([]);
    const [selectedRole, setSelectedRole] = useState([]);
    const [selectedUser, setSelectedUser] = useState([]);
    const [selectedAssetType, setSelectedAssetType] = useState([]);
    const [selectedAsset, setSelectedAsset] = useState([]);
    //due date management json
    // const [dueDateDataJSON, setDueDateDataJSON] = useState({});
    const [dueSoonValue, setDueSoonValue] = useState("0")
    const [overDueValue, setOverDueValue] = useState("0")
    const [postEffect, setPostEffect] = useState(0)

    const [selectedRecipientType, setSelectedRecipientType] = useState('auto');

    //call API to get the dropdown value of notification type
    const getNotificationTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Notifications/Config/List`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                setNotificationTriggers(response.data);
                setDataReady(true);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    //call API to get the dropdown value of business units
    const getBusinessUnitsTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/BusinessUnit/List`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                response.data.map((d => {
                        d.name = " "+d.name.charAt(0).toUpperCase()+d.name.slice(1);
                 }));
                setBusinessTriggers(response.data);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    //call API to get the dropdown value of locations
    const getLocationsTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Location/List`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                response.data.map((d => {
                        d.location_name = " "+d.location_name.charAt(0).toUpperCase()+d.location_name.slice(1);
                 }));
                setLocationTriggers(response.data);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    const getRolesTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/RolePermission/Get/All`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                response.data.map((d => {
                    d.role = " "+d.role.charAt(0).toUpperCase()+d.role.slice(1);
                }));
                setRoleTriggers(response.data);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    //call API to get the dropdown value of users
    const getUsersTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Get/All`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                response.data.map((d => {
                    d.accounting_email = " "+d.accounting_email;
                 }));
                setUserTriggers(response.data);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    //call API to get the dropdown value of asset and asset type
    const getAssetTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/All `, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                setAssetTriggers(response.data);
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    //call API to get the dropdown value of asset and asset type
    const getAssetTypeTriggers = () => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/List `, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                setAssetTypes(response.data);
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    const handleFunctionRadioSelect = (receipt_type) => {
        setSelectedRecipientType(receipt_type);
        notificationUpdateDataJSON['recipient_type'] = receipt_type;
        postNotificationConfigUpdate();
    }

    const postNotificationConfigUpdate = () => {
        if (!notificationUpdateDataJSON) {
            return;
        }
        notificationUpdateDataJSON['active'] = selectedNotification['active'] ? 1 : 0;
        notificationUpdateDataJSON['enable'] = selectedNotification['enable']; // not sure what is this for for now
        notificationUpdateDataJSON['custom_text'] = customText;

        // pre check
        // if (!notificationUpdateDataJSON['recipient_type']) {
        //     // notificationUpdateDataJSON['recipient_type'] = selectedNotification['recipient_type'];
        //     return;
        // }
        let myurl = `${Constants.ENDPOINT_PREFIX}/api/v1/Notifications/Config/Edit`;
        let mydata = {};
        mydata[selectedNotification.id] = notificationUpdateDataJSON;
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .post(myurl, mydata, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                //this line is for testing
                //after updating the data, we reload all the data
                getNotificationTriggers();
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    }

    //due date management radio selected
    const handleRadioAssetChange = (e) => {
        dueDateDataJSON['radio-asset'] = e.target.value;
        postAssetUpdate();
    }

    // post asset info update (in due date management)
    const postAssetUpdate = () => {
        const cancelTokenSource = axios.CancelToken.source();
        let mydata = {}
        let myurl = `${Constants.ENDPOINT_PREFIX}/api/v1/`;
        if (!dueDateDataJSON) {
            // if nothing done
            return;
        }
        if (!dueDateDataJSON['radio-asset']) {
            // if not select "By Asset Class" or "By Asset"
            return;
        }
        if (dueDateDataJSON['radio-asset'] === 'asset') {
            // selected asset
            if (!dueDateDataJSON['asset'] ) {
                // no asset selected
                return;
            }
            mydata['VIN'] = dueDateDataJSON['asset'];
            myurl += 'Assets/Update';
        } else {
            // selected asset type
            if (!dueDateDataJSON['asset-type'] ) {
                // no asset type selected
                return;
            }
            mydata['id'] = dueDateDataJSON['asset-type'];
            myurl += 'AssetType/Update';
        }
        mydata['overdue_date_variance'] = dueDateDataJSON['over-due'] ? dueDateDataJSON['over-due'] : 0;
        mydata['due_soon_date_variance'] = dueDateDataJSON['due-soon'] ? dueDateDataJSON['due-soon'] : 0;
        axios
            .post(myurl, mydata, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                //this line is for testing
            })
            .catch((error) => {
                ConsoleHelper(error);
            });
    };

    // theres probably a better way to do this, regardless makes the get api call if the data is not present
    useEffect(() => {
        if (!dataReady) {
            getNotificationTriggers();
        }
    });

    //updates selectedValue with no input lag (useState has input lag)
    useEffect(() => {
        selectedNotification = selectedValue
            ? notificationTriggers.filter((e) => e.name === selectedValue)[0]
            : {};
        getBusinessUnitsTriggers();
        getLocationsTriggers();
        getUsersTriggers();
        getRolesTriggers();
        getAssetTriggers();
        getAssetTypeTriggers();
        setSelectedRecipientType(selectedNotification.recipient_type);
        setCustomText(selectedNotification.custom_text);
        // update notification data to be update
        notificationUpdateDataJSON = {
            fields: selectedNotification.fields,
            triggers: selectedNotification.triggers,
        }
    }, [selectedValue]);

    useEffect(() => {
        setIsActivated(selectedNotification.active);
    }, [selectedNotification.active]);

    useEffect(() => {
        if (postEffect !== 0) {
            postNotificationConfigUpdate();
        }
    }, [postEffect])

    // compare business units passed from server and set it as default in the page
    useEffect(() => {
        // once business triggers are updated
        let businessUnit = selectedNotification['business_units'];
        if (businessUnit) {
            let businessUnits = businessUnit.split('-');
            if (businessUnits.length > 1) {
                let selectedBU = [];
                for (let i = 1; i < businessUnits.length; i++) {
                    let id = businessUnits[i];
                    businessTriggers.forEach((each) => {
                        if (each['business_unit_id'].toString() === id) {
                            selectedBU.push({name: each['name'], code: each['business_unit_id']});
                        }
                    })
                }

                setSelectedBusinessUnit(selectedBU);
            }
        } else {
            setSelectedBusinessUnit([]);
        }
    }, [businessTriggers])

    // compare locations passed from server and set it as default in the page
    useEffect(() => {
        // once business triggers are updated
        let location = selectedNotification['locations'];
        if (location) {
            let locations = location.split('-');
            if (locations.length > 1) {
                let selectLoc = [];
                for (let i = 1; i < locations.length; i++) {
                    let id = locations[i];
                    locationTriggers.forEach((each) => {
                        if (each['location_id'].toString() === id) {
                            selectLoc.push({name: each['location_name'], code: each['location_id']});
                        }
                    })
                }
                setSelectedLocation(selectLoc);
            }
        } else {
            setSelectedLocation([]);
        }
    }, [locationTriggers])


    // compare roles passed from server and set it as default in the page
    useEffect(() => {
        // once business triggers are updated
        let role = selectedNotification['roles'];
        if (role) {
            let roles = role.split('-');
            if (roles.length > 1) {
                let selectRole = [];
                for (let i = 1; i < roles.length; i++) {
                    let id = roles[i];
                    roleTriggers.forEach((each) => {
                        if (each['id'].toString() === id) {
                            selectRole.push({name: each['role'], code: each['id']});
                        }
                    })
                }
                setSelectedRole(selectRole);
            }
        } else {
            setSelectedRole([]);
        }
    }, [roleTriggers])


    // compare users passed from server and set it as default in the page
    useEffect(() => {
        // once business triggers are updated
        let user = selectedNotification['users'];
        if (user) {
            let users = user.split('-');
            if (users.length > 1) {
                let selectUser = [];
                for (let i = 1; i < users.length; i++) {
                    let id = users[i];
                    userTriggers.forEach((each) => {
                        if (each['detailed_user_id'].toString() === id) {
                            selectUser.push({name: each['email'], code: each['detailed_user_id']});
                        }
                    })
                }
                setSelectedUser(selectUser);
            }
        } else {
            setSelectedUser([]);
        }
    }, [userTriggers])

    const createButtonGroups = () => {
        const recipientTypes = [
            {
                value: 'business_units',
                label: 'Business Units',
                receipt_type: 'business_unit',
                func: setSelectedBusinessUnit,
                selectedValue: selectedBusinessUnit,
                options: businessTriggers?.map(e => ({
                    name: e.name,
                    code: e.business_unit_id
                }))
            },
            {
                value: 'locations',
                label: 'Locations',
                receipt_type: 'location',
                func: setSelectedLocation,
                selectedValue: selectedLocation,
                options: locationTriggers?.map(e => ({
                    name: e.location_name,
                    code: e.location_id
                }))
            },
            {
                value: 'roles',
                label: 'Roles',
                receipt_type: 'role',
                func: setSelectedRole,
                selectedValue: selectedRole,
                options: roleTriggers?.map(e => ({
                    name: e.role,
                    code: e.id
                }))
            },
            {
                value: 'users',
                label: 'Users',
                receipt_type: 'user',
                func: setSelectedUser,
                selectedValue: selectedUser,
                options: userTriggers?.map(e => ({
                    name: e.email,
                    code: e.detailed_user_id
                }))
            }
        ];

        const handleMultiSelectChange = (key, values, func) => {
            if(func){
            func(values);
            }
            let result = '-';
            values.forEach(each => {
                result += each.code + '-';
            });
            notificationUpdateDataJSON[key] = result;
            postNotificationConfigUpdate();
        };

        return (
            <div className={"custom-radio-btn"}>
                {recipientTypes.map(type => (
                    <div className="input-switch-function-container" key={type.value}>
                        <RadioButton
                            inputId={type.value}
                            name="input-switch-function"
                            value={type.value}
                            checked={selectedRecipientType === type.receipt_type}
                            onChange={(e) => {
                                handleFunctionRadioSelect(type.receipt_type)
                            }}
                            className="input-switch-function"
                        />
                        <p className="input-label">{type.label}</p>
                        <div className = "input-dropdown">
                        <MultiSelectDropdown
                            className="input-function-dropdown"
                            value={type.selectedValue}
                            options={type.options}
                            onChange={e => handleMultiSelectChange(type.value, e.value, type.func)}
                        />
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="manage-notifications">
            {/* top part of the page, title and icon only */}
            <div className="header-container">
                <PanelHeader
                    icon={faUsers}
                    text={t("accountOptions.manage_notifications_title")}
                    disableBg
                />
            </div>
            {/* main panel containing page contents */}
            <div className="main-container">
                {dataReady ? (
                    <div>
                        {/* dropdown for selecting a notification trigger, stores what the user selects in selectedValue (only the name of the notification) */}
                        <Dropdown
                            value={selectedValue}
                            onChange={(e) => {
                                setSelectedValue(e.target.value);
                            }}
                            options={notificationTriggers.map((e) => e.name)}
                            placeholder="Select a notification"
                            className="notification-dropdown"
                            panelClassName="notification-dropdown-panel"
                        />
                        {/* based on whether a notification from the dropdown is selcted, display page contents */}
                        {selectedValue ? (
                            <div className="input-container">
                                <div className="input-switch-container">
                                    {/* currently not working, selectedNotification.active goes from true -> false -> undefined (or something like that) idk why */}
                                    <div style={{display: "flex"}}>
                                        <p style={{width: "120px", marginBottom: "10px"}}>Activate</p>
                                        <InputSwitch
                                            checked={isActivated}
                                            onChange={(e) => {
                                                setIsActivated(e.value);
                                                selectedNotification['active'] = !selectedNotification['active'];
                                                postNotificationConfigUpdate();
                                            }}
                                        />
                                    </div>
                                    {/*<div style={{display: "flex"}}>*/}
                                    {/*    <p style={{width: "120px"}}>Originator Copy</p>*/}
                                    {/*    <InputSwitch*/}
                                    {/*        checked={isEnabled}*/}
                                    {/*        onChange={(e) => {*/}
                                    {/*            setIsEnabled(e.value);*/}
                                    {/*            selectedNotification['active'] = !selectedNotification['active'];*/}
                                    {/*        }}*/}
                                    {/*    />*/}
                                    {/*</div>*/}
                                </div>
                                <div style={{display: "flex"}}>
                                    {createButtonGroups()}
                                    <div>
                                        <p>Custom Email Message</p>
                                        <div>
                                            <input type="text"
                                                   value={"  "+customText}
                                                   onBlur={() => {
                                                       setPostEffect(postEffect + 1);
                                                   }}
                                                   onChange={(e) => {
                                                      if(e.target.value.length>2){
                                                       setCustomText(e.target.value.substring(2));
                                                      }
                                                      else{
                                                        setCustomText("");
                                                      }
                                                       // postNotificationConfigUpdate();
                                                   }}
                                                   style={{marginTop: "10px", height: "150px", width: "300px"}}/>
                                        </div>
                                    </div>
                                </div>
                                {selectedNotification.id === 9 && (
                                    <div className="input-asset-container">
                                        <h4>
                                            Due Date Management
                                        </h4>
                                        <br></br>
                                        <div style={{display: "flex"}}>
                                            <div>
                                                <div className="input-switch-function-container">
                                                    <input type="radio" className="input-switch-function" onChange={handleRadioAssetChange} value="assetClass"
                                                           name="input-switch-asset"/>
                                                    <p className="input-label">By Asset Class</p>
                                                    <MultiSelectDropdown
                                                        classNames="input-function-dropdown"
                                                        value={selectedAssetType}
                                                        options={assetTypeTriggers && assetTypeTriggers.map((e) => {
                                                            return {name: e.name, code: e.id}
                                                        })}
                                                        onChange={(e) => {
                                                            setSelectedAssetType(e.value)
                                                            dueDateDataJSON['asset-type'] = e.value[0] ? e.value[0].code : null;
                                                            postAssetUpdate();
                                                        }}
                                                        selectionLimit={1}
                                                    />
                                                </div>
                                                <div className="input-switch-function-container">
                                                    <input type="radio" className="input-switch-function" onChange={handleRadioAssetChange} value="asset"
                                                           name="input-switch-asset"/>
                                                    <p className="input-label">By Asset</p>
                                                    <MultiSelectDropdown
                                                        classNames="input-function-dropdown"
                                                        value={selectedAsset}
                                                        options={assetTriggers && assetTriggers.map((e) => {
                                                            return {name: e.VIN + "-" + e.unit_number, vin: e.VIN}
                                                        })}

                                                        onChange={(e) => {
                                                            setSelectedAsset(e.value)
                                                            dueDateDataJSON['asset'] = e.value[0] ? e.value[0].vin : null;
                                                            postAssetUpdate();
                                                        }}
                                                        selectionLimit={1}
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <div className="input-switch-function-container-r">
                                                    <div className = "input-switch-function-container-r-first">
                                                    <p>Due Soon</p>
                                                    </div>
                                                    <div className = "input-switch-function-container-r-second">
                                                    <input className="input-switch-function-r" type="number" min="0"
                                                           max="365"
                                                           value={dueSoonValue}
                                                           onChange={(e) => {
                                                               setDueSoonValue(e.target.value)
                                                               dueDateDataJSON['due-soon'] = e.target.value;
                                                               postAssetUpdate();
                                                           }}
                                                    />
                                                    </div>
                                                    <p>Days</p>
                                                    <div className = "b-a">
                                                    <FormDropdown options={
                                                        [
                                                            {name: "Before", code: 0}, {name: "After", code: 1}
                                                        ]
                                                    } onChange={(code) => {
                                                        if (code === 0) {
                                                            // before
                                                            let date = dueDateDataJSON['due-soon'] ? dueDateDataJSON['due-soon'] : 0;
                                                            if (date > 0) {
                                                                date = -date;
                                                            }
                                                            dueDateDataJSON['due-soon'] = date;
                                                        } else {
                                                            // after
                                                            let date = dueDateDataJSON['due-soon'] ? dueDateDataJSON['due-soon'] : 0;
                                                            if (date < 0) {
                                                                date = -date;
                                                            }
                                                            dueDateDataJSON['due-soon'] = date;
                                                        }
                                                        postAssetUpdate();
                                                    }}
                                                    plain_dropdown
                                                    />
                                                    </div>
                                                </div>

                                                <div className="input-switch-function-container-r">
                                                    <div className = "input-switch-function-container-r-first">
                                                    <p>Overdue</p>
                                                    </div>
                                                    <div className = "input-switch-function-container-r-second">
                                                    <input className="input-switch-function-r" type="number" min="0"
                                                           max="365"
                                                           value={overDueValue}
                                                           onChange={(e) => {
                                                               setOverDueValue(e.target.value)
                                                               dueDateDataJSON['over-due'] = e.target.value;
                                                               postAssetUpdate();
                                                           }}/>
                                                           </div>
                                                    <p>Days</p>
                                                    <div className = "b-a">
                                                    <FormDropdown  options={
                                                        [
                                                            {name: "Before", code: 0}, {name: "After", code: 1}
                                                        ]
                                                    } onChange={(code) => {
                                                        if (code === 0) {
                                                            // before
                                                            let date = dueDateDataJSON['over-due'] ? dueDateDataJSON['over-due'] : 0;
                                                            if (date > 0) {
                                                                date = -date;
                                                            }
                                                            dueDateDataJSON['over-due'] = date;
                                                        } else {
                                                            // after
                                                            let date = dueDateDataJSON['over-due'] ? dueDateDataJSON['over-due'] : 0;
                                                            if (date < 0) {
                                                                date = -date;
                                                            }
                                                            dueDateDataJSON['over-due'] = date;
                                                        }
                                                        postAssetUpdate();
                                                    }}
                                                    plain_dropdown
                                                    />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                    </div>
                                )}
                            </div>
                        ) : (
                            <p></p>
                        )}
                    </div>
                ) : (
                    <p></p>
                )}
            </div>
        </div>
    );
};

function DropdownSearchBox(state) {

}

export default ManageNotifications;
