import pyodbc
import os

os.mkdir("Generated")
os.mkdir(os.path.join("Generated", "ENT"))
os.mkdir(os.path.join("Generated", "BAL"))
os.mkdir(os.path.join("Generated", "DAL"))

serverName = input("Enter your SQL Server Instance Name: ")
dbName = input("Enter Database Name: ")

print("\nNote: Enter 0 if you don't use Username and Password else press Enter")
chk = input()

sqlConnStr = ''

if chk != '0':
    uid = input("Enter Username: ")
    password = input("Enter Password: ")
    sqlConnStr = (
        'DRIVER={SQL Server Native Client 11.0};'
        'SERVER='+serverName+';'
        'DATABASE='+dbName+';'
        'UID='+uid+';'
        'PWD='+dbName+';'
        'Trusted_Connection=YES'
    )
else:
    sqlConnStr = (
        'DRIVER={SQL Server Native Client 11.0};'
        'SERVER='+serverName+';'
        'DATABASE='+dbName+';'
        'Trusted_Connection=YES'
    )

conn = pyodbc.connect(sqlConnStr)
curs = conn.cursor()

allTables = []

def convert(columnType):
    if columnType == "int":
        return str("SqlInt32")
    if columnType == "varchar":
        return str("SqlString")
    if columnType == "datetime":
        return str("SqlDateTime")

def generateEntity(columnName, columnType):

    code = "\t#region "+columnName+"\n\n"

    code += "\tprotected " + str(convert(columnType)) + \
        " _" + columnName + ";\n\n"
    code += "\tpublic " + str(convert(columnType)) + " " + columnName + "\n"
    code += "\t{\n"
    code += "\t\tget\n"
    code += "\t\t{\n"
    code += "\t\t\treturn _" + columnName + ";\n"
    code += "\t\t}\n"
    code += "\t\tset\n"
    code += "\t\t{\n"
    code += "\t\t\t_" + columnName + " = value;\n"
    code += "\t\t}\n"
    code += "\t}\n\n\t#endregion\n\n"

    return code

def generateBAL(tableName):
    name = tableName
    codeBAL = 'using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Web;\nusing System.Data;\nusing AddressBook.DAL;\nusing System.Data.SqlTypes;\n\n/// <summary>\n/// Summary description for ' + \
        tableName+'BAL\n/// </summary>\npublic class '+tableName+'BAL \n{\n'
    codeBAL += '\t#region Local Variables\n    private string _Message;\n\n    public string Message\n    {\n        get\n        {\n            return _Message;\n        }\n        set\n        {\n            _Message = value;\n        }\n    }\n    #endregion\n\n    #region Insert Operation\n    public Boolean Insert(' + name + 'ENT ent' + name + ')\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + 'DAL();\n\n        if (dal' + name + '.Insert(ent' + name + '))\n        {\n            return true;\n        }\n        else\n        {\n            Message = dal' + name + '.Message;\n            return false;\n        }\n    }\n    #endregion\n\n    #region Update Operation\n    public Boolean Update(' + name + 'ENT ent' + name + ')\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + 'DAL();\n\n        if (dal' + name + '.Update(ent' + name + '))\n        {\n            return true;\n        }\n        else\n        {\n            Message = dal' + name + '.Message;\n            return false;\n        }\n    }\n    #endregion\n\n    #region Delete Operation\n    public Boolean Delete(SqlInt32 ' + \
        name + 'ID)\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + 'DAL();\n\n        if (dal' + name + '.Delete(' + name + 'ID))\n        {\n            return true;\n        }\n        else\n        {\n            Message = dal' + name + '.Message;\n            return false;\n        }\n    }\n    #endregion\n\n    #region Select Operation\n\n    #region SelectAll\n    public DataTable SelectAll()\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + 'DAL();\n        return dal' + name + \
        '.SelectAll();\n    }\n    #endregion\n\n    #region Select For Dropdown List\n    public DataTable SelectForDropdownList()\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + 'DAL();\n        return dal' + name + \
        '.SelectForDropdownList();\n    }\n    #endregion\n\n    #region SelectByPK\n    public ' + name + 'ENT SelectByPK(SqlInt32 ' + name + \
        'ID)\n    {\n        ' + name + 'DAL dal' + name + ' = new ' + name + \
        'DAL();\n        return dal' + name + '.SelectByPK(' + \
        name + 'ID);\n    }\n    #endregion\n\n    #endregion\n}'

    f = open('Generated/BAL/' + tableName + 'BAL.cs', 'x')
    f.write(codeBAL)
    f.close()

def generateDAL(tableName):
    paramsInsert = ''
    for i in curs.columns(table=tableName):
        if(i.column_name != 'CreationDate' and i.column_name != tableName + 'ID'):
            paramsInsert += 'objCmd.Parameters.AddWithValue("@' + i.column_name + '", ent'+ tableName +'.' +  i.column_name +');\n\t\t\t\t\t\t'
    
    paramsUpdate = ''
    for i in curs.columns(table=tableName):
        if(i.column_name != 'CreationDate' and i.column_name != 'UserID'):
            paramsUpdate += 'objCmd.Parameters.AddWithValue("@' + i.column_name + '", ent'+ tableName +'.' +  i.column_name +');\n\t\t\t\t\t\t'

    paramsDelete = 'objCmd.Parameters.AddWithValue("@' + tableName + 'ID", ' + tableName + 'ID);\n\t\t\t\t\t\t'

    ReadNSet = ''
    name = tableName

    for i in curs.columns(table=tableName):
        if((i.column_name != tableName + 'ID') and (i.column_name != "CreationDate") and ((i.column_name != "UserID"))):
            if('ID' in i.column_name):
                ReadNSet += 'if (!objSDR["' + i.column_name + '"].Equals(DBNull.Value))\n                                    ent' + name + '.' + i.column_name + ' = Convert.ToInt32(objSDR["' + i.column_name + '"]);\n\n\t\t\t\t\t\t\t\t'
            else:
                ReadNSet += 'if (!objSDR["' + i.column_name + '"].Equals(DBNull.Value))\n                                    ent' + name + '.' + i.column_name + ' = Convert.ToString(objSDR["' + i.column_name + '"]);\n\n\t\t\t\t\t\t\t\t'

    codeDAL = 'using AddressBook;\nusing System;\nusing System.Collections.Generic;\nusing System.Data;\nusing System.Data.SqlClient;\nusing System.Data.SqlTypes;\nusing System.Linq;\nusing System.Web;\n/// <summary>\n/// Summary description for '+name+'DAL\n/// </summary>\n\npublic class '+name+'DAL : DatabaseConfig\n{'
    codeDAL += '\n\t#region Local Variables\n\n        private string _Message;\n\n        public string Message\n        {\n            get\n            {\n                return _Message;\n            }\n            set\n            {\n                _Message = value;\n            }\n        }\n        #endregion\n\n        #region Insert Operation\n        public Boolean Insert(' + name + 'ENT ent' + name + ')\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n\n                        #region Prepare Command\n                        objCmd.CommandType = CommandType.StoredProcedure;\n                        objCmd.CommandText = "PR_' + name + '_Insert";\n                        '+ paramsInsert +'\n                        #endregion\n\n                        objCmd.ExecuteNonQuery();\n\n                        return true;\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return false;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return false;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n        #region Update Operation\n        public Boolean Update(' + name + 'ENT ent' + name + ')\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n\n                        #region Prepare Command\n                        objCmd.CommandType = CommandType.StoredProcedure;\n                        objCmd.CommandText = "PR_' + name + '_UpdateByPK";\n                        '+ paramsUpdate +'\n                        #endregion\n\n                        objCmd.ExecuteNonQuery();\n                        return true;\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return false;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return false;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n        #region Delete Operation\n        public Boolean Delete(SqlInt32 ' + name + 'ID)\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n\n                        #region Prepare Command\n                        objCmd.CommandType = CommandType.StoredProcedure;\n                        objCmd.CommandText = "PR_' + tableName + '_DeleteByPK";\n\n                        '+ paramsDelete +'\n                        #endregion\n\n\n                        objCmd.ExecuteNonQuery();\n\n                        return true;\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return false;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return false;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n\t#region Select Operation\n\n        #region SelectAll\n        public DataTable SelectAll()\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n                        #region Prepare Command\n                        objCmd.CommandType = CommandType.StoredProcedure;\n                        objCmd.CommandText = "PR_' + \
        name + '_SelectAll";\n                        #endregion\n\n                        #region Read Data and return DataTable\n                        DataTable dt = new DataTable();\n\n                        using (SqlDataReader objSDR = objCmd.ExecuteReader())\n                        {\n                            dt.Load(objSDR);\n                        }\n                        return dt;\n                        #endregion\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return null;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return null;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n        #region SelectForDropdownList\n        public DataTable SelectForDropdownList()\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n\n                        DataTable dt = new DataTable();\n\n                        return dt;\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return null;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return null;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n        #region SelectByPK\n        public ' + \
        name + 'ENT SelectByPK(SqlInt32 ' + name + 'ID)\n        {\n            using (SqlConnection objConn = new SqlConnection(ConnectionString))\n            {\n                objConn.Open();\n\n                using (SqlCommand objCmd = objConn.CreateCommand())\n                {\n                    try\n                    {\n                        #region Prepare Command\n                        objCmd.CommandType = CommandType.StoredProcedure;\n                        objCmd.CommandText = "PR_'+ name +'_SelectByPK";\n                        objCmd.Parameters.AddWithValue("@'+ name +'ID", '+ name +'ID);\n                        #endregion \n\n                        #region Read Data and return ENT\n\n                        ' + name + 'ENT ent'+ name +' = new ' + name + 'ENT();\n\n                        SqlDataReader objSDR = objCmd.ExecuteReader();\n\n                        if (objSDR.HasRows)\n                        {\n                            while (objSDR.Read())\n                            {\n                                ' + ReadNSet +'\n\n                                break;\n                            }\n                        }\n\n                        return ent' + name + ';\n\n                        #endregion;\n                    }\n                    catch (SqlException sqlex)\n                    {\n                        Message = sqlex.InnerException.Message;\n                        return null;\n                    }\n                    catch (Exception ex)\n                    {\n                        Message = ex.InnerException.Message;\n                        return null;\n                    }\n                    finally\n                    {\n                        if (objConn.State == ConnectionState.Open)\n                            objConn.Close();\n                    }\n                }\n            }\n        }\n        #endregion\n\n        #endregion\n}'

    f = open('Generated/DAL/' + tableName + 'DAL.cs', 'x')
    f.write(codeDAL)
    f.close()


def getAllDatabaseTables(curs):
    for row in curs.tables(tableType='TABLE').fetchall():
        if curs.primaryKeys(row.table_name, row.table_cat, row.table_schem).fetchone():
            allTables.append(row.table_name)
            print(row.table_name)
            codeNull = ''
            for i in curs.columns(table=row.table_name): 
                codeNull += '\t\t_' + i.column_name + ' = ' + convert(i.type_name.split(' ')[0]) + '.Null;\n'
            codeENT = 'using System;\nusing System.Collections.Generic;\nusing System.Data.SqlTypes;\nusing System.Linq;\nusing System.Web;\n\n/// <summary>\n/// Summary description for ' + \
                row.table_name+'ENT'+'\n/// </summary>\npublic class ' + \
                row.table_name+'ENT' + \
                '\n{\n\t#region Constructor\n\n\tpublic ' + \
                row.table_name+'ENT()\n\t{\n'+codeNull+'\t}\n\n\t#endregion\n\n'
            for i in curs.columns(table=row.table_name):
                codeENT += generateEntity(i.column_name,
                                          i.type_name.split(' ')[0])
            codeENT += '\n}'


            f = open('Generated/ENT/' + row.table_name + 'ENT.cs', 'x')
            f.write(codeENT)
            f.close()

            generateBAL(row.table_name)

            generateDAL(row.table_name)

    return allTables


getAllDatabaseTables(curs)
