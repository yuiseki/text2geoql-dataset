// Important note: SubArea: United States/California
[out:json][timeout:30000];
area["name:en"="California"]["admin_level"=4]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=6](area.searchArea);
);
out meta;
