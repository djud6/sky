# SkyIT React Share Components

## Table of Contents

1. [Tabs](#tabs)
1. [Tables](#tables)

---
## TAB

Tabs organize content across different screens, data sets, and other interactions.

### Usage

```javascript
// Import both Tabs and TabPanel component
import Tabs from '../components/ShareComponents/Tab/Tabs';
import TabPanel from '../components/ShareComponents/Tab/TabPanel';

// Preparing the data for the tab title
let tabTitle = ["UNRESOLVED ISSUES", "RESOLVED ISSUE"];

// Passing the tabTitles to the Tabs component
<Tabs tabTitles={tabTitle} >
    // Use TabPanel to display subpages
    <TabPanel index={0}>
        Page #1
    </TabPanel>
    // Index will map to the tableTitles index
    <TabPanel index={1}>
        Page #2
    </TabPanel>
</Tabs>            
```

### Properties

#### Tabs
| propName  | type                  | default               | isRequired                  |
| --------  | --------------------- | --------------------- | --------------------------- |
| children  | `ReactNode`           |                       | No                          |
| tabTitles | `string[]`            |                       | Yes                         |

#### TabPanel
| propName  | type                  | default               | isRequired                  |
| --------  | --------------------- | --------------------- | --------------------------- |
| children  | `ReactNode`           |                       | No                          |
| index     | `number`              |                       | Yes                         |


---
## Tables

Data tables display sets of data across rows and columns.


### Usage

```javascript
// Import Table component
import Table from "../ShareComponents/Table/Table";

// Preparing the data for the table headers, it's a string[]
let tableHeaders = ["VIN", "Issue Type", "Vendor","Issue Details"];
// Preparing the data for thee table body, it's a Object[] with structure as {id:xxx,cells:[xxx,xxx]}
let tableData = [{ id: "K5S7H9", cells: ["K5S7H9", (<span className="text-danger">Critical</span>), "Vendor A", "Broken Engines"] }];
// Preparing the data for pagination, it's a Object with strucure as follow
let paginationParam = { totalPages: totalRequestPages, currentPage: currentRequestPage, onPageChangeHandle: handleRequestPageClick }
// If you want to show spinner while loading the data, use this param
let dataReady = false; 

// Call back function to handle the pagination page changes
function handleRequestPageClick({ selected: selectedPage }) {
    setCurrentRequestPage(selectedPage);
}

// Passing the tableHeaders and tableData to the Table component
<Table tableHeaders={tableHeaders} tableData={tableData} pagination={paginationParam} hasSelection dataReady={dataReady} />
```

### Properties

#### Tables
| propName      | type                  | default               | isRequired                  |
| ------------- | --------------------- | --------------------- | --------------------------- |
| tableHeaders  | `string[]`            |                       | Yes                         |
| tableData     | `Object[]`            |                       | Yes                         |
| pagination    | `Object  `            | null                  | No                          |
| hasSelection  | `Boolean  `           | false                 | No                          |
| dataReady     | `Boolean  `           | true                  | No                          |