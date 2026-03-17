import React, { useEffect, useState } from "react";
function index() {
  const [data, setData] = useState([]);
  useEffect(() => {
    const fetchdata = async () => {
      try {
        const response = await fetch("http://localhost:5000/transactions", {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });
        if (response.ok) {
          const result = await response.json();
          console.log("Success:", result);
          setData(Array.isArray(result) ? result : []);
        } else {
          console.error("Submission failed");
        }
      } catch (error) {
        console.error("Error during login:", error);
      }
    };
    fetchdata();
  }, []);
  return (
    <div>
      <h1>Transactions</h1>
      <ul>
        {data.map((item, index) => (
          <li key={index}>
            {typeof item === "object" ? JSON.stringify(item) : String(item)}
          </li>
        ))}
      </ul>
    </div>
  );
}
export default index;
