# UAM RLS Documentation v2 (Markdown Migration)

> Source migrated from <File>UAM RLS Documentation v2.docx</File>. The SharePoint URL you provided was not retrievable via enterprise search in this session, so this Markdown is generated from the uploaded copy of the document. citeturn8search1

## Table of contents
- [Banking Unit](#banking-unit)
  - [Part 1: Set Up Row-Level Security (RLS)](#part-1-set-up-row-level-security-rls)
    - [A. Data Modeling](#a-data-modeling)
    - [B. Create RLS Roles](#b-create-rls-roles)
    - [C. Final Step: Publish and Test](#c-final-step-publish-and-test)
- [Connection](#connection)
  - [Part 1: Set Up Row-Level Security (RLS)](#part-1-set-up-row-level-security-rls-1)
    - [A. Data Modeling](#a-data-modeling-1)
    - [B. Create RLS Roles](#b-create-rls-roles-1)
    - [C. Final Step: Publish and Test](#c-final-step-publish-and-test-1)

---

## Banking Unit

This section provides a step-by-step guide for implementing Row-Level Security (RLS) combined with a dynamic user interface (UI) that responds to a user's access level. citeturn8search1

### Part 1: Set Up Row-Level Security (RLS)

This section covers the data modeling and DAX rules required to secure your report. citeturn8search1

#### A. Data Modeling

##### Add the `Security_Table`

Import your security table (from Dataflow). citeturn8search1

**Security_Table source (as documented):** citeturn8search1

| Field | Value | Notes |
|---|---:|---|
| WorkSpace | 0e897f86-95d5-495d-9265-30fe7748ee10 | GRM Commons |
| DataFlowID | cf3352f9-c271-4486-923b-e447b63010a1 | UAM Security |
| Table | Security_Table | |

**Advanced Query (Power Query M):** citeturn8search1
```powerquery
let
  Source = PowerPlatform.Dataflows(null),
  Workspaces = Source{[Id="Workspaces"]}[Data],
  #"0e897f86-95d5-495d-9265-30fe7748ee10" = Workspaces{[workspaceId="0e897f86-95d5-495d-9265-30fe7748ee10"]}[Data],
  #"d05c2625-602e-4432-ad9c-d8add0926b7c" = #"0e897f86-95d5-495d-9265-30fe7748ee10"{[dataflowId="cf3352f9-c271-4486-923b-e447b63010a1"]}[Data],
  Security_Table_ = #"d05c2625-602e-4432-ad9c-d8add0926b7c"{[entity="Security_Table", version=""]}[Data]
in
  Security_Table_
```

##### Create a Banking Unit dimension table

This dimension table is critical. It will connect your security table to your data. citeturn8search1

Go to the **Data** view, select **New Table**, and use this DAX: citeturn8search1
```DAX
Dim_Banking_Unit =
FILTER(
  DISTINCT(YourFactTable[BANKING_UNIT_TRANSIT_CD]),
  NOT(ISBLANK(YourFactTable[BANKING_UNIT_TRANSIT_CD]))
)
```

> Replace `YourFactTable` with your main data table (example in the document: `eCARDS_Connection`). citeturn8search1

##### Build model relationships

- Create a relationship: `Dim_Banking_Unit[BANKING_UNIT_TRANSIT_CD]` → `YourFactTable[BANKING_UNIT_TRANSIT_CD]` citeturn8search1
- **Cross-filter direction:** Single (from `Dim_Banking_Unit` to `YourFactTable`) citeturn8search1
- **Note:** ensure relationships flow correctly so slicers and filters are also restricted by RLS; security should flow from `Dim_Banking_Unit` → fact tables and other slicer tables. citeturn8search1

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->

#### B. Create RLS Roles

- Go to the **Modeling** tab and click **Manage roles**.
- Create a new role (e.g., `User Filter`). citeturn8search1

**Rule 1 (on `Dim_Banking_Unit`):** scalable DAX rule that filters report data. citeturn8search1
```DAX
VAR ME = USERPRINCIPALNAME()
VAR AllowedBankingUnits =
  CALCULATETABLE(
    VALUES(Security_Table[transit_number]),
    Security_Table[email] = ME
  )
VAR IsRestrictedUser = NOT(ISEMPTY(AllowedBankingUnits))
RETURN
  IF(
    IsRestrictedUser,
    Dim_Banking_Unit[BANKING_UNIT_TRANSIT_CD] IN AllowedBankingUnits,
    TRUE()
  )
```

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->

#### C. Final Step: Publish and Test

- **Publish** the report to the Power BI Service. citeturn8search1
- **Grant** user groups access: manage permissions via **Direct Access** and add users or groups. citeturn8search1
- **Configure Security:** in the service, open the dataset settings for the semantic model, find **Security**, and add user groups to the `User Filter` role. citeturn8search1
- **Test Security Roles:** use **Test as role** on the semantic model; under **Viewing**, select a report to view. citeturn8search1
- Use **Now viewing as** to test the user’s access. citeturn8search1

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->

---

## Connection

This section provides a step-by-step guide for implementing Row-Level Security (RLS) combined with a dynamic user interface (UI) that responds to a user's access level. citeturn8search1

### Part 1: Set Up Row-Level Security (RLS)

This section covers the data modeling and DAX rules required to secure your report. citeturn8search1

#### A. Data Modeling

##### Add the `Security_Table`

Import your security table (from Dataflow). citeturn8search1

**Security_Table source (as documented):** citeturn8search1

| Field | Value | Notes |
|---|---:|---|
| WorkSpace | 0e897f86-95d5-495d-9265-30fe7748ee10 | GRM Commons |
| DataFlowID | cf3352f9-c271-4486-923b-e447b63010a1 | UAM Security |
| Table | Security_Table | |

**Advanced Query (Power Query M):** citeturn8search1
```powerquery
let
  Source = PowerPlatform.Dataflows(null),
  Workspaces = Source{[Id="Workspaces"]}[Data],
  #"0e897f86-95d5-495d-9265-30fe7748ee10" = Workspaces{[workspaceId="0e897f86-95d5-495d-9265-30fe7748ee10"]}[Data],
  #"d05c2625-602e-4432-ad9c-d8add0926b7c" = #"0e897f86-95d5-495d-9265-30fe7748ee10"{[dataflowId="cf3352f9-c271-4486-923b-e447b63010a1"]}[Data],
  Security_Table_ = #"d05c2625-602e-4432-ad9c-d8add0926b7c"{[entity="Security_Table", version=""]}[Data]
in
  Security_Table_
```

##### Create three tables

Go to the **Data** view, select **New Table**, and use the following DAX patterns: citeturn8search1

1) **Dimension table – `Dim_Banking_Unit`** (unique list of banking units): citeturn8search1
```DAX
Dim_Banking_Unit =
FILTER(
  DISTINCT(YourFactTable[BANKING_UNIT_TRANSIT_CD]),
  NOT(ISBLANK(YourFactTable[BANKING_UNIT_TRANSIT_CD]))
)
```

2) **Dimension table – `Dim_Connection`** (unique list of connection names + a placeholder row): citeturn8search1
```DAX
Dim_Connection =
UNION(
  SUMMARIZE(YourFactTable, YourFactTable[Connection_Name]),
  ROW("Connection_Name", "Please select the Connection")
)
```

3) **Bridge table – `Bridge_Banking_Unit_Connection`** (banking unit ↔ connection mapping): citeturn8search1
```DAX
Bridge_Banking_Unit_Connection =
FILTER(
  SUMMARIZE(
    YourFactTable,
    YourFactTable[BANKING_UNIT_TRANSIT_CD],
    YourFactTable[Connection_Name]
  ),
  NOT(ISBLANK([BANKING_UNIT_TRANSIT_CD]))
    && NOT(ISBLANK(YourFactTable[Connection_Name]))
)
```

> Replace `YourFactTable` with your main data table (example in the document: `eCARDS_Connection`). citeturn8search1

##### Build model relationships

Create four relationships (the 4th is optional depending on whether there is another fact table): citeturn8search1

1. `Dim_Banking_Unit[BANKING_UNIT_TRANSIT_CD]` → `Bridge_Banking_Unit_Connection[BANKING_UNIT_TRANSIT_CD]`  
   - Cross-filter direction: **Single** (from `Dim_Banking_Unit` to `Bridge_Banking_Unit_Connection`) citeturn8search1
2. `Bridge_Banking_Unit_Connection[Connection_Name]` ↔ `Dim_Connection[Connection_Name]`  
   - Cross-filter direction: **Bi-directional** (between bridge and `Dim_Connection`) citeturn8search1
3. `Dim_Connection[Connection_Name]` → `YourFactTable[Connection_Name]`  
   - Cross-filter direction: **Single** (from `Dim_Connection` to `YourFactTable`) citeturn8search1
4. `Dim_Connection[Connection_Name]` → `YourFactTable2[Connection_Name]` (optional)  
   - Cross-filter direction: **Single** (from `Dim_Connection` to `YourFactTable2`) citeturn8search1

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->

#### B. Create RLS Roles

- Go to the **Modeling** tab and click **Manage roles**.
- Create a new role (e.g., `User Filter`). citeturn8search1

**Rule 1 (on `Dim_Connection`):** scalable DAX rule that filters report data. citeturn8search1
```DAX
VAR ME = USERPRINCIPALNAME()
VAR AllowedBankingUnits =
  CALCULATETABLE(
    VALUES(Security_Table[transit_number]),
    Security_Table[email] = ME
  )
VAR AllowedConnections =
  CALCULATETABLE(
    VALUES(Bridge_Banking_Unit_Connection[Connection_Name])
  )
  ,
  FILTER(
    ALL(Bridge_Banking_Unit_Connection),
    Bridge_Banking_Unit_Connection[BANKING_UNIT_TRANSIT_CD] IN AllowedBankingUnits
  )
VAR PlacerholderName = {"Please select the Connection"}
VAR FinalAccessList = UNION(AllowedConnections, PlacerholderName)
VAR IsRestrictedUser = NOT(ISEMPTY(AllowedBankingUnits))
RETURN
  IF(
    IsRestrictedUser,
    Dim_Connection[Connection_Name] IN FinalAccessList,
    TRUE()
  )
```

> Note: The DAX above mirrors the document text, including the placeholder and union logic. citeturn8search1

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->

#### C. Final Step: Publish and Test

- **Publish** the report to the Power BI Service. citeturn8search1
- **Grant** user groups access: manage permissions via **Direct Access** and add users or groups. citeturn8search1
- **Configure Security:** in the service, open the dataset settings for the semantic model, find **Security**, and add user groups to the `User Filter` role. citeturn8search1
- **Test Security Roles:** use **Test as role** on the semantic model; under **Viewing**, select a report to view. citeturn8search1
- Use **Now viewing as** to test the user’s access. citeturn8search1

<!-- Screenshot(s) present in DOCX were omitted in this Markdown export. -->
