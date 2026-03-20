[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Ukyo Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
