[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Asahi Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
