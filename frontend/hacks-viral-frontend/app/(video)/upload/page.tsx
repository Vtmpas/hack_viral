import UploadForm from "@/components/video/upload-form";

export const metadata = {
  title: "Upload video - Tsukizard",
  description: "Page description",
};

export default function UploadVideo() {
  return (
    <section>
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="py-12 md:py-20">
          {/* Section header */}
          <div className="pb-12 text-center">
            <h1 className="animate-[gradient_6s_linear_infinite] bg-[linear-gradient(to_right,theme(colors.gray.200),theme(colors.indigo.200),theme(colors.gray.50),theme(colors.indigo.300),theme(colors.gray.200))] bg-[length:200%_auto] bg-clip-text font-nacelle text-3xl font-semibold text-transparent md:text-4xl">
              Выберете видео
            </h1>
          </div>
          {/* Upload form */}
          <UploadForm />
        </div>
      </div>
    </section>
  );
}
