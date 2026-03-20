[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Minato"]->.inner;
(
  nwr["office"="diplomatic"](area.inner)(area.outer);
);
out geom;
