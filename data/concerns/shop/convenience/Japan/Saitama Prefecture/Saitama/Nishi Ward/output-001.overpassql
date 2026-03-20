[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
