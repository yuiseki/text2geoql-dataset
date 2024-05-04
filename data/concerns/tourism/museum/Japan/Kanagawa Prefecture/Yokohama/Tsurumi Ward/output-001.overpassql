[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Tsurumi Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
