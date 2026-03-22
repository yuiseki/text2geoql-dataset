[out:json][timeout:30];
area["name:en"="Piedmont"]->.outer;
area["name:en"="Turin"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;