[out:json][timeout:30];
area["name:en"="Ho Chi Minh City"]->.outer;
area["name:en"="Ho Chi Minh City"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;