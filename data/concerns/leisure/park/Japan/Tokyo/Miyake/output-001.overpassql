[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Miyake"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
