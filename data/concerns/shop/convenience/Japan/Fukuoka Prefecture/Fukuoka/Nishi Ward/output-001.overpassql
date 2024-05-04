[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
