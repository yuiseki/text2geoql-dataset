[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shibuya"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
