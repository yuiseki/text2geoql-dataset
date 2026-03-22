[out:json][timeout:30];
area["name:en"="Lombardy"]->.outer;
area["name:en"="Milan"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;