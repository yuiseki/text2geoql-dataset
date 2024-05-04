[out:json][timeout:30000];
area["name:en"="Kobe"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
