[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Higashikurume"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
