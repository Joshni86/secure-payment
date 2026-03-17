import Link from "next/link";
import React, { useState, useEffect } from "react";
function index() {
  return (
    <div>
      <nav>
        <Link href="./login">Login</Link>
      </nav>
      <h1 className="content-center">Ahoy! Welcome to Payments Secure</h1>
    </div>
  );
}
export default index;
