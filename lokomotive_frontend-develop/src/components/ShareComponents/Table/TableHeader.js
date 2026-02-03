import React from 'react';

const TableHeader = ({ tableHeaders }) => {
	return (
		<thead className="thead-dark">
			<tr>
				{tableHeaders.map((text, index) => {
					return (<th key={index} scope="col" className="text-uppercase">{text}</th>);
				})}
			</tr>
		</thead>
	);
};

export default TableHeader;
