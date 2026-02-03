import React from "react";

const TableRow = ({ cells, onClick, selection = false }) => {
  if (!!!cells) return null;

  return (
    <tr onClick={onClick} className={selection ? "bg-tablehighlight" : ""}>
      {cells.map((cell, i) => {
        return <td key={i}>{cell}</td>;
      })}
    </tr>
  );
};

export default TableRow;
