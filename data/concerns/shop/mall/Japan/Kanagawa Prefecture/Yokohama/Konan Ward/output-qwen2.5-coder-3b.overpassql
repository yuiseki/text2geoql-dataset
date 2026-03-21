[out:json][timeout:30];
area["name:ja"="横浜市"]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
