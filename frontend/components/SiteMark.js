export function SiteMark({ className = "", inverted = false }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <span
        className={`relative grid h-8 w-8 place-items-center rounded-full ${
          inverted ? "bg-cream text-wine" : "bg-contrast text-on-contrast"
        }`}
      >
        <span className="absolute left-2 top-2 h-2 w-2 rounded-full bg-moss" />
        <span className="absolute right-2 bottom-2 h-2 w-2 rounded-full bg-clay" />
      </span>
      <span className="font-serif text-xl tracking-tight">
        Life<span className={inverted ? "text-ember" : "text-wine"}>Assist</span>
      </span>
    </span>
  );
}
