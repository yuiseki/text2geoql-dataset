[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Higashinari Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
