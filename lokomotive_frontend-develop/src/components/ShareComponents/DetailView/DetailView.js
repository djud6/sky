import React from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";

const DetailView = ({ children, title, editBtn, actionBtns, headers, values }) => {
  let tableValues = [{ ...values }];
  const titleView = <h3 className="p-my-2">{title}</h3>;

  const headerView = (
    <div className="detail-view-header p-d-flex p-flex-column p-flex-md-row p-jc-between table-header">
      <div className="p-d-flex p-ai-center">
        {titleView}
        {editBtn}
      </div>
      {actionBtns}
    </div>
  );

  const bodyTemplate = (data, props) => {
    return (
      <React.Fragment>
        <span className="p-column-title">{props.header}</span>
        <span className="p-body-template">{data[props.field]}</span>
      </React.Fragment>
    );
  };

  return (
    <div>
      <DataTable value={tableValues} header={headerView} className="p-datatable-sm detail-view">
        {headers.map((header, index) => (
          <Column
            className="detail-view-col-header"
            key={index}
            body={bodyTemplate}
            field={index.toString()}
            header={header}
          />
        ))}
      </DataTable>
      <div className="p-shadow-1">{children}</div>
    </div>
  );
};

export default DetailView;