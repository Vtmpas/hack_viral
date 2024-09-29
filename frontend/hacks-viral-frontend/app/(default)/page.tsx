export const metadata = {
  title: "Home - Tsukizard",
  description: "Page description",
};

import PageIllustration from "@/components/ui/page-illustration";
import WelcomeHome from "@/components/default/welcome-home";


export default function Home() {
  return (
    <>
      <PageIllustration />
      <WelcomeHome />
    </>
  );
}
