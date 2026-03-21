[out:json][timeout:30];
area["name:ja"="神奈川県"]->.outer;
area["name:ja"="横浜市"]->.inner;
(
  nwr["memorial"](area.inner)(area.outer);
);
out geom;
