[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Minuma Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
