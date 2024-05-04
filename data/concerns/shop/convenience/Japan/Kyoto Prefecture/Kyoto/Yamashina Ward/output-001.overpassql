[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Yamashina Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
