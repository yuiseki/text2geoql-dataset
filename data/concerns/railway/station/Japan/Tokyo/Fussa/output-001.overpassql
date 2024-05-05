[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Fussa"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
