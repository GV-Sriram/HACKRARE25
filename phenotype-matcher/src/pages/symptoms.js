import { getSession } from "next-auth/react";

export default function SymptomsPage({ user }) {
  return (
    <div>
      <h1>Welcome, {user?.name || "Guest"}!</h1>
      <p>Enter your symptoms below:</p>
      <input type="text" placeholder="Describe your symptoms..." />
      <button>Submit</button>
    </div>
  );
}

// Protect the page so only logged-in users can access it
export async function getServerSideProps(context) {
  const session = await getSession(context);

  if (!session) {
    return {
      redirect: {
        destination: "/login", // Redirect to login if not authenticated
        permanent: false,
      },
    };
  }

  return {
    props: { user: session.user },
  };
}

