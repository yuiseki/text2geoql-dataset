[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
