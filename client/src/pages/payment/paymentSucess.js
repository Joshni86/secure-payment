import Link from "next/link";
function paymentSucess() {
  return (
    <div>
      <h1>Payment Successful</h1>
      <Link href="./dashboard">Go to Dashboard</Link>
    </div>
  );
}
export default paymentSucess;
