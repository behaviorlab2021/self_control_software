import React from "react";

function SessionInfo({ session }) {
  return (
    <div id="session_info">
      <table
        style={{
          border: "1px solid black",
          width: "100%",
          marginBottom: "10px",
        }}
      >
        <tbody>
          {Object.entries(session).map(([key, value]) => (
            <tr key={key}>
              <td style={{ border: "1px solid black", width: "50%" }}>
                <strong>{key}</strong>
              </td>
              <td
                style={{
                  border: "1px solid black",
                  width: "50%",
                  textAlign: "center",
                }}
              >
                {JSON.stringify(value, null, 2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SessionInfo;
