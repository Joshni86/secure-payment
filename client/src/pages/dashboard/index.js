import Link from "next/link";
import React from "react";
function index() {
  return (
    <div>
      <nav>
        <Link href="./login">Logout</Link>
        <Link href="../">Home</Link>
        <Link href="./payment">Payments</Link>
      </nav>
      <h1 className="content-center">Do Payments securely</h1>
    </div>
  );
}
export default index;
