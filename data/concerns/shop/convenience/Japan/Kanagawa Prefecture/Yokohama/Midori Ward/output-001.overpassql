[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
