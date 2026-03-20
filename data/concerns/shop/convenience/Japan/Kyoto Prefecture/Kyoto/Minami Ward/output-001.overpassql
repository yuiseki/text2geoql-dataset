[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
