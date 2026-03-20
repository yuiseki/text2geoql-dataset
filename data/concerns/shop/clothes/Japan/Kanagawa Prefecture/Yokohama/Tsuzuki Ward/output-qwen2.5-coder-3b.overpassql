[out:json][timeout:30];
area["name:en"="Tsuzuki Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["shop"~"clothes"](area.inner)(area.outer);
);
out geom;
