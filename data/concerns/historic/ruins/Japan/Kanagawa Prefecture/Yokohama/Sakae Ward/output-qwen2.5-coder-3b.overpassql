[out:json][timeout:30];
area["name:ja"="横浜市"][boundary=administrative]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;
