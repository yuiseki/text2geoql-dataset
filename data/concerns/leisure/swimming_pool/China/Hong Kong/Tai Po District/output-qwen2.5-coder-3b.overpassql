[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh-hk"="香港"];
(
  nwr["leisure"="swimming_pool"](area.outer);
);
out geom;
