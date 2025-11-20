import type { Route } from "./+types/home";
import Dashboard from "../pages/dashboard";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "USA." },
    { name: "description", content: "Understand , Summarize and Analyse" },
  ];
}

export default function Home() {
  return <Dashboard />;
}
