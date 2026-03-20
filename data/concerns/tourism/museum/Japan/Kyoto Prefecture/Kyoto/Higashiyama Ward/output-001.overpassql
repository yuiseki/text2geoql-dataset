[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Higashiyama Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
