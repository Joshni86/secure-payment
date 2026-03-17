"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
function index() {
  const [amount, setAmount] = useState(0.0);
  const [currency, setCurrency] = useState("");
  const [merchantId, setMerchantId] = useState(0);
  const router = useRouter();
  const handleSubmit = async (event) => {
    event.preventDefault();
    const data = {
      amount: amount,
      currency: currency,
      merchantId: merchantId,
    };

    try {
      const response = await fetch("http://localhost:5000/payment", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        const result = await response.json();
        console.log("Success:", result);
        //redirect to payment
        router.push("./payment/paymentSucess");
      } else {
        console.error("Submission failed");
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };
  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="amount">Amount:</label>
      <input
        id="amount"
        type="number"
        step="0.01"
        min="0"
        name="amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />
      <br></br>
      <label htmlFor="currency">Currency:</label>
      <input
        id="currency"
        type="text"
        name="currency"
        value={currency}
        onChange={(e) => setCurrency(e.target.value)}
        required
      />
      <br></br>
      <label htmlFor="merchantId">Merchant ID:</label>
      <input
        id="merchantId"
        type="number"
        min="0"
        name="merchantId"
        value={merchantId}
        onChange={(e) => setMerchantId(e.target.value)}
        required
      />
      <br></br>
      <button type="submit">Submit</button>
    </form>
  );
}
export default index;
