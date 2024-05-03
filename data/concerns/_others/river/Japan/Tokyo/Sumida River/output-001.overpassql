[out:json][timeout:30000];
area["name:en"="Japan"]->.outer;
area["name:en"="Tokyo"]->.inner;
(
  nwr["name:en"="Sumida River"](area.inner)(area.outer);
);
out geom;
