[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kodaira"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
