import React from "react";
import { useTranslation } from "react-i18next";
import { Card } from "primereact/card";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";

const TableRow = ({ title, data }) => {
  return (
    <tr>
      <th scope="row">{title}</th>
      <td>{data}</td>
    </tr>
  );
};

const VehicleTable = ({ vehicle, roleReady }) => {
  const { t } = useTranslation();

  return (
    <>
      {vehicle && roleReady ? (
        <Card className="ml-4 mr-4">
          <div className="p-d-flex p-flex-column p-flex-md-row">
            <div>
              <table className="table p-mb-2 p-mr-2" frame="void">
                <tbody>
                  <TableRow title={t("assetDetailPanel.vin_label")} data={vehicle[0].VIN} />
                  <TableRow
                    title={t("assetDetailPanel.asset_type_label")}
                    data={vehicle[0].asset_type}
                  />
                  <TableRow
                    title={t("assetDetailPanel.business_unit_label")}
                    data={vehicle[0].businessUnit}
                  />
                  <TableRow title={t("assetDetailPanel.status_label")} data={vehicle[0].status} />
                  <TableRow
                    title={t("assetDetailPanel.location_label")}
                    data={vehicle[0].current_location}
                  />
                  <TableRow
                    title={t("assetDetailPanel.manufacturer_label")}
                    data={vehicle[0].manufacturer || t("general.not_applicable")}
                  />
                </tbody>
              </table>
            </div>
            <div>
              <table className="table p-mb-2 p-mr-2" frame="void">
                <tbody>
                  <TableRow
                    title={t("assetDetailPanel.company_label")}
                    data={vehicle[0].company || t("general.not_applicable")}
                  />
                  <TableRow
                    title={t("assetDetailPanel.year_of_manufacture")}
                    data={vehicle[0].date_of_manufacture || t("general.not_applicable")}
                  />
                  <TableRow
                    title={t("assetDetailPanel.fuel_type_label")}
                    data={vehicle[0].fuel_type || t("general.not_applicable")}
                  />
                  <TableRow
                    title={t("assetDetailPanel.license_plate_label")}
                    data={vehicle[0].license_plate || t("general.not_applicable")}
                  />
                  {vehicle[0].hours_or_mileage.toLowerCase() === "both" ? (
                    <TableRow
                      title={`${t("assetDetailPanel.mileage_label")} / ${t(
                        "assetDetailPanel.hours_label"
                      )}`}
                      data={
                        `${t("assetDetailPanel.mileage_label")}: ${vehicle[0].mileage}, 
                        ${t("assetDetailPanel.hours_label")}: ${vehicle[0].hours}` ||
                        t("general.not_applicable")
                      }
                    />
                  ) : vehicle[0].hours_or_mileage.toLowerCase() === "mileage" ? (
                    <TableRow
                      title={t("assetDetailPanel.mileage_label")}
                      data={vehicle[0].mileage || t("general.not_applicable")}
                    />
                  ) : (
                    <TableRow
                      title={t("assetDetailPanel.hours_label")}
                      data={vehicle[0].hours || t("general.not_applicable")}
                    />
                  )}
                  {vehicle[0].last_process !== "Null" ? (
                    <TableRow
                      title={t("assetDetailPanel.last_process_label")}
                      data={vehicle[0].last_process}
                    />
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      ) : (
        <FullWidthSkeleton height={"260px"} />
      )}
    </>
  );
};

export default VehicleTable;
