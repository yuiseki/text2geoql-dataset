[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["railway"~"subway"](area.inner)(area.outer);
);
out geom;
