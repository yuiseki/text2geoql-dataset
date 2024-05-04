[out:json][timeout:30000];
area["name:en"="Fukuoka Prefecture"]->.outer;
area["name:en"="Sawara Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
