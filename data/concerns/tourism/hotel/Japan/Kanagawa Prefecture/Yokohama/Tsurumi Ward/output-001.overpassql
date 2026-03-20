[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Tsurumi Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
