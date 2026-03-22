[out:json][timeout:30];
area["name:en"="Hamburg"]->.outer;
area["name:en"="Hamburg"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;