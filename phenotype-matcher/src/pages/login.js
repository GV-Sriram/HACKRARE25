import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/router";



export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    if (!result.error) {
      router.push("/symptoms"); // Redirect to symptoms page after login
    } else {
      alert("Invalid credentials, try again!");
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <form onSubmit={handleSubmit} style={{ padding: "20px", border: "1px solid #ccc", borderRadius: "5px" }}>
        <h2>Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <button type="submit" style={{ backgroundColor: "blue", color: "white", padding: "10px", width: "100%" }}>
          Login
        </button>
      </form>
    </div>
  );
}

